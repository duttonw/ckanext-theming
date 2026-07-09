
# Publish via GitHub actions


For this to work. You must first ensure that you have a connection
endpoint setup at pypi.org

Then when you update the toml version and but a 'version' tag follwoing ```*.*.*```

It will run the publish.yml file re-running test.yml to ensure that its not a dud.


For new projects visit:

https://pypi.org/manage/account/publishing/

If already existing visit

```https://pypi.org/manage/project/${PYTHON MODULE}/settings/publishing/``` i.e.  https://pypi.org/manage/project/ckanext-theming/settings/publishing/

### Add a new publisher

GitHub Tab:

 * PyPI Project Name (required) -- When new module, else won't be shown

   i.e. ```ckanext-theming```

   The project that will be created on PyPI when this publisher is used

* Owner (required)

  i.e. ```DataShades```

  The GitHub organization name or GitHub username that owns the repository

* Repository name (required)

  i.e.  ```ckanext-theming```

  The name of the GitHub repository that contains the publishing workflow

* Workflow name (required)

  ```publish.yml```

  The filename of the publishing workflow. This file should exist in the .github/workflows/ directory in the repository configured above.


* Environment name (required)

  ```pypi```

  The name of the GitHub Actions environment that the above workflow uses for publishing. This should be configured under the repository's settings. While not required, a dedicated publishing environment is strongly encouraged, especially if your repository has maintainers with commit access who shouldn't have PyPI publishing access.



## Notes

If this workflow is copied to another repo/module. ensure you change the publish protections so that it runs as that user. This is needed so that if a repo is 'forked' it does not try and publish as a non owner
