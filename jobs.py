import ast
import json
import os
import urllib.request
from flask import Flask, render_template

jenkins_url = os.environ.get("JENKINS", "http://jenkins:8080")
view = os.environ.get("VIEW", "Development")

app = Flask(__name__)


@app.route("/")
def home():
    jobs = {}
    buildstatus = []
    url = jenkins_url + "/view/" + view + "/api/json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    for job in data['jobs']:
        jobs.update({job['name']: job['url']})

    for job in jobs:
        url = jobs[job] + "api/json"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        if not data['builds']:
            build = "NONE"
        else:
            url_lb = data['builds'][0]['url'] + "api/json"
            resp_lb = urllib.request.urlopen(url_lb)
            data_lb = json.loads(resp_lb.read())
            build = data_lb['actions'][0]['causes'][0]['shortDescription']
        build = Build(strip_build(job), data['color'], build)
        buildstatus.append(build)

    return render_template('jobs.html', status=buildstatus, view=view)


class Build:
    def __init__(self, job, color, lastbuild):
        self.job = job
        self.color = color
        self.lastbuild = lastbuild


def strip_build(build):
    if str.lower(build).startswith("build"):
        return build[5:]
    else:
        return build
