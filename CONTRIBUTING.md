# CONTRIBUTING to Dash Chart Editor

Thanks for your interest in contributing to this open source project.

### Setting up the environment
Here are the steps for building and testing locally:

```
# in your working directory
$ git clone https://github.com/BSd3v/dash-chart-editor.git
$ cd dash-chart-editor

$ python3 -m venv venv
# activate the virtualenv
# on windows `venv\scripts\activate`
# on some linux / mac environments, use `.` instead of `source`
$ source venv/bin/activate

# install dependencies
$ pip install -r requirements.txt 
$ pip install -r /tests/requirements.txt
$ npm ci

# build
$ npm run build  

# install in editable mode
$ pip install -e .
```
To run the examples

```
$ pip install -r /examples/requirements.txt
```
Then run the demo apps in the `/examples` folder



### Pull Requests

Pull requests are welcome. Thanks for contributing to Dash Chart Editor.

1. [Fork](https://help.github.com/articles/fork-a-repo/) the project, clone your fork,
   and configure the remotes:

```bash
   # Clone your fork of the repo into the current directory
   git clone https://github.com/<your-username>/dash-chart-editor.git
   # Navigate to the newly cloned directory
   cd dash-chart-editor
   # Assign the original repo to a remote called "upstream"
   git remote add upstream https://github.com/BSd3v/dash-chart-editor.git
```

2. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout dev
   git pull upstream dev
   ```

3. Create a new topic branch (off the dev project development branch) to
   contain your feature, change, or fix:

   ```bash
   git checkout -b <topic-branch-name>
   ```

4. Commit your changes in logical chunks. Please adhere to these [git commit
   message guidelines](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
   or your code is unlikely be merged into the main project. Use Git's
   [interactive rebase](https://help.github.com/articles/about-git-rebase/)
   feature to tidy up your commits before making them public.

5. Locally merge (or rebase) the upstream development branch into your topic branch:

   ```bash
   git pull [--rebase] upstream dev
   ```

6. Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

7. [Open a Pull Request](https://help.github.com/articles/about-pull-requests/)
   with a clear title and description against the `dev` branch.

------------
------------

### Maintainers only - Create a production build and publish:

1. Build your code:
    ```
    $ npm run build
    ```
2. Create a Python distribution
    ```
    $ python setup.py sdist bdist_wheel
    ```
    This will create source and wheel distribution in the generated the `dist/` folder.
    See [PyPA](https://packaging.python.org/guides/distributing-packages-using-setuptools/#packaging-your-project)
    for more information.

3. Test your tarball by copying it into a new environment and installing it locally:
    ```
    $ pip install dash_chart_editor-0.0.1.tar.gz
    ```

4. If it works, then you can publish the component to NPM and PyPI:
    1. Publish on PyPI
        ```
        $ twine upload dist/*
        ```
    2. Cleanup the dist folder (optional)
        ```
        $ rm -rf dist
        ```
    3. Publish on NPM (Optional if chosen False in `publish_on_npm`)
        ```
        $ npm publish
        ```
        _Publishing your component to NPM will make the JavaScript bundles available on the unpkg CDN. By default, Dash serves the component library's CSS and JS locally, but if you choose to publish the package to NPM you can set `serve_locally` to `False` and you may see faster load times._
