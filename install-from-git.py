import os
import re
import subprocess
import shutil

import sublime
import sublime_plugin

class GoodClass(object):

    @property
    def underscore_name(self):
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__name__)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @property
    def settings(self):
        return sublime.load_settings('install-from-git.sublime-settings')

    def save_settings(self):
        sublime.save_settings('install-from-git.sublime-settings')


class InstallFromGit(sublime_plugin.WindowCommand, GoodClass):

    def run(self, **kwargs):
        getattr(self, kwargs.get('cmd', 'no_cmd'), lambda: None)(**kwargs)

    def _run(self, cmd):
        popen_arg_list = {
            'shell': False,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
        self.proc = subprocess.Popen(cmd, **popen_arg_list)

    def reinstall_all(self, **kwargs):
        settings = self.settings
        repositories = settings.get('repositories', [])
        default_package_name_pattern = settings.get('default_package_name_pattern', r'([a-zA-Z0-9_-]+)/[a-zA-Z0-9_]+\.git')
        package_name_patterns = settings.get('package_name_patterns', {})
        for url in repositories:
            package_name_pattern = default_package_name_pattern
            for k, v in package_name_patterns.items():
                if k in url:
                    package_name_pattern = v
                    break
            package_name = next(re.finditer(package_name_pattern, url)).group(1)
            package_path = os.path.join(sublime.packages_path(), package_name)
            if os.path.exists(package_path):
                shutil.rmtree(package_path)
                os.mkdir(package_path)
                os
            print(os.path.exists(package_path))
            print('install-from-git: installing package', package_name)
            cmd = ['git', '--version']
            self._run(cmd)
            info, error = self.proc.communicate()
            print(info, error)
            cmd = ['git', 'clone', url, package_path]
            self._run(cmd)
            info, error = self.proc.communicate()
            if error:
                sublime.error_message('install-from-git:\n\n'+error.decode('utf-8'))

    def add_repository(self, **kwargs):
        self.window.show_input_panel(
            'Git repository url',
            '',
            self.on_done,
            self.on_change,
            self.on_cancel
        )

    def on_done(self, repo_url):
        repo_url = repo_url.strip()

        if not re.findall(r'\.git', repo_url):
            sublime.error_message('Unable to add the repository {0} since it does not ends with .git'.format(repo_url))
            return

        repositories = self.settings.get('repositories', [])
        repositories.append(repo_url)
        self.settings.set('repositories', list(set(repositories)))
        self.save_settings()
        sublime.status_message('Repository %s successfully added' % repo_url)

    def on_change(self, input_str):
        pass

    def on_cancel(self, input_str):
        pass
