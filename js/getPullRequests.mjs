import { Octokit } from 'octokit';
import { exists, mkdir, readFileSync, writeFileSync } from 'fs';


async function fn_err(err, repo, number, str) {
    console.log(str + ": " + repo + " number: " + number);
    console.log(
        "Error Name: " + err.name + " (" + err.status + ")\n" +
        "Error Message: " + err.message);

    if (err.status == 403) {
        console.log("Stopped...");
        await new Promise(resolve => setTimeout(resolve, 600000));
        console.log("Starting... [DONE]");
    }
}

async function getIssue(owner, repo, issue_number) {
    let closed_by = "";

    try {
        const issue = await octokit.rest.issues.get({
            owner: owner,
            repo: repo,
            issue_number: issue_number
        });

        if (issue.data.closed_by != null) {
            closed_by = issue.data.closed_by.login;
        }
        else {
            closed_by = "NULL";
        }

        return closed_by;
    } catch (err) {
        fn_err(err, repo, issue_number, "issues.get");
        return null;
    }
}

async function getPull(owner, repo, pull_number) {
    let merged_by = "";
    try {
        const p = await octokit.rest.pulls.get({
            owner: owner,
            repo: repo,
            pull_number: pull_number
        });

        if (p.data.merged_by != null) {
            merged_by = p.data.merged_by.login;
        }
        else {
            merged_by = "NULL";
        }

        return merged_by;
    } catch (err) {
        fn_err(err, repo, pull_number, "pulls.get");
        return null;
    }
}

async function getReviews(owner, repo, pull_number) {
    let reviewMap = [];

    try {
        const reviews = await octokit.rest.pulls.listReviews({
            owner: owner,
            repo: repo,
            pull_number: pull_number
        });

        reviewMap = reviews.data.map(review => {
            return {
                user: (review.user) ? review.user.login : "",
                state: review.state,
                submitted_at: review.submitted_at,
                commit_id: review.commit_id
            };
        });

        return reviewMap;
    } catch (err) {
        fn_err(err, repo, pull_number, "listReviews");
        return null;
    }
}


async function getCommits(owner, repo, pull_number) {
    let commitsMap = [];

    try {
        const commits = await octokit.rest.pulls.listCommits({
            owner: owner,
            repo: repo,
            pull_number: pull_number
        });

        commitsMap = commits.data.map(co => {
            return {
                commit_id: co.sha,
                author: co.commit.committer.name,
                commited_at: co.commit.committer.date
            };
        });
        return commitsMap;
    } catch (err) {
        fn_err(err, repo, pull_number, "listCommits");
        return null;
    }
}


let fname = '../repos.json';
const octokit = new Octokit();
// const octokit = new Octokit({ auth: `personal-access-tokens` }); // https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api#using-personal-access-tokens

   
exists('../data/pull_requests/', (exists) => {
    if (!exists) {
        mkdir('../data/pull_requests/', (err) => {
            if (err) {
                return console.error(err);
            }
        });        
    }
}); 


try {
    const data = readFileSync(fname, 'utf8');
    const repositorios = JSON.parse(data);

    let j = 1;
    for (const r of repositorios) {
        if (r.clone == 0) {
            continue;
        }

        try {
            let k = 1;
            let i = 1;
            let users = [];

            let reviewData = [];
            let fileName = '../data/pull_requests/' + r.repo + '.json';

            console.log(j + " of " + repositorios.length);
            console.log(fileName);

            j += 1;

            const pulls = await octokit.paginate(octokit.rest.pulls.list,
            {
                owner: r.owner,
                repo: r.repo,
                state: 'closed',
                per_page: 100
            });

            console.log("pushing reviewData");
            pulls.forEach(pull => {
                reviewData.push({
                    pull_number: pull.number,
                    created_by: pull.user.login,
                    created_at: pull.created_at,
                    closed_by: "",
                    closed_at: pull.closed_at,
                    merged_by: "",
                    merged_at: pull.merged_at,
                    downloaded: 0,
                    requested_reviewers: pull.requested_reviewers.map(rv => rv.login),
                    requested_teams: pull.requested_teams.map(rt => rt.name)
                });
            });

            console.log("writeFileSync: " + await reviewData.length);
            writeFileSync(fileName, JSON.stringify(await reviewData.sort((a, b) => {
                return a.pull_number - b.pull_number;
            }), null, 4));

            for (const pull of reviewData) {
                if (pull.downloaded == 0) {
                    let resp = null;

                    if (pull.closed_at != null) {
                        while (resp == null) {
                            resp = await getIssue(r.owner, r.repo, pull.pull_number);
                        }
                        pull.closed_by = resp;
                    }

                    if (pull.merged_at != null) {
                        resp = null;
                        while (resp == null) {
                            resp = await getPull(r.owner, r.repo, pull.pull_number);
                        }
                        pull.merged_by = resp;
                    }

                    resp = null;
                    while (resp == null) {
                        resp = await getReviews(r.owner, r.repo, pull.pull_number);
                    }
                    pull.reviews = resp;

                    resp = null;
                    while (resp == null) {
                        resp = await getCommits(r.owner, r.repo, pull.pull_number);
                    }
                    pull.commits = resp;
                    pull.downloaded = 1;

                    i += 1;

                    if (i % 200 == 0) {
                        console.log("[getData] Saving:" + k + " of " + reviewData.length);
                        writeFileSync(fileName, JSON.stringify(reviewData, null, 4));
                        console.log("[getData] DONE");
                    }
                }
                else if (pull.downloaded == 1) {
                    for (const co of pull.commits) {
                        try {
                            const c = await octokit.rest.repos.getCommit({
                              owner: r.owner,
                              repo: r.repo,
                              ref: co.commit_id,
                            });

                            let commited_files = []

                            if (c.data.files) {
                                c.data.files.forEach(f => {
                                    commited_files.push(f.filename)
                                });
                            }

                            co.files = await commited_files;
                            pull.downloaded = 2;

                            i += 1;

                            if (i % 200 == 0) {
                                console.log("[getCommit] Saving...");
                                writeFileSync(fileName, JSON.stringify(reviewData, null, 4));
                                console.log("[getCommit] DONE");
                            }
                        } catch (err) {
                            fn_err(err, r.repo, pull.pull_number, "getCommit");
                        }
                    }
                }
                else if (pull.downloaded == 2) {
                    try {
                        if (!(pull.created_by in users)) {
                            users[pull.created_by] = {};

                            try {
                                const u = await octokit.rest.users.getByUsername({
                                    username: pull.created_by
                                });

                                let name = pull.closed_by;
                                if (u.data.name) {
                                    name = u.data.name;
                                }

                                users[pull.created_by] = {'login': pull.created_by, 'name': name, 'email': u.data.email};
                            } catch (err) {
                                console.log(err);
                            }
                        }
                            
                        if (pull.closed_by != "" && pull.closed_by != "NULL") {
                            if (!(pull.closed_by in users)) {
                                users[pull.closed_by] = {};
                                try {
                                    const u = await octokit.rest.users.getByUsername({
                                        username: pull.closed_by
                                    });

                                    let name = pull.closed_by;
                                    if (u.data.name) {
                                        name = u.data.name;
                                    }

                                    users[pull.closed_by] = {'login': pull.closed_by, 'name': name, 'email': u.data.email};
                                } catch (err) {
                                    console.log(err);
                                }
                            }
                        }

                        if (pull.merged_by != "" && pull.merged_by != "") {
                            if (!(pull.merged_by in users)) {
                                users[pull.merged_by] = {};

                                try {
                                    const u = await octokit.rest.users.getByUsername({
                                        username: pull.merged_by
                                    });

                                    let name = pull.closed_by;
                                    if (u.data.name) {
                                        name = u.data.name;
                                    }

                                    users[pull.merged_by] = {'login': pull.merged_by, 'name': name, 'email': u.data.email};
                                } catch (err) {
                                    console.log(err);
                                }
                            }
                        }

                        if (users[pull.created_by] && users[pull.created_by].name != "") {
                            pull.created_by = users[pull.created_by].name;
                        }
                        
                        if (users[pull.closed_by] && users[pull.closed_by].name != "") {
                            pull.closed_by = users[pull.closed_by].name;
                        }

                        if (users[pull.merged_by] && users[pull.merged_by].name != "") {
                            pull.merged_by = users[pull.merged_by].name;
                        }

                        pull.downloaded = 3

                        i += 1;

                        if (i % 200 == 0) {
                            console.log("[getByUsername] Saving... ");
                            writeFileSync(fileName, JSON.stringify(reviewData, null, 4));
                            console.log("[getByUsername] DONE");
                        }
                    } catch (err) {
                        fn_err(err, r.repo, pull.pull_number, "getByUsername");
                    }
                }

                k += 1;

                if (k % 200 == 0 && i % 200 != 0) {
                    console.log(k + " of " + reviewData.length);
                }
            }

        } catch (err) {
            console.log(JSON.stringify(r));
            console.log(err);

            if (err.status == 403) {
                console.log("Stopped...");
                await new Promise(resolve => setTimeout(resolve, 600000));
                console.log("JSON.stringify Starting... [DONE]");
            }
        }
        finally {
            if (i != 1) {
                console.log("writeFileSync: " + fileName);
                writeFileSync(fileName, JSON.stringify(reviewData, null, 4));
            }

            console.log("[DONE]");
        }
    }
} catch (err) {
    console.log(`Error handling file from disk: ${err}`);
}
