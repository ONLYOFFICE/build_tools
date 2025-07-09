#!/usr/bin/env python3
"""
Git Operations Script
Provides functionality to clone repositories and create branches.
Uses existing methods from base module and integrates with release.py patterns.
"""

import sys
import argparse
import logging
from typing import Dict

# Add parent directory to path to import modules
sys.path.append('../')
import base
import config
import dependence

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GitOperations:
    """Class to handle git clone and branch creation using existing base module methods."""
    
    def __init__(self, branding: str = "onlyoffice", base_branch: str = "develop", 
                 branding_url: str = "ONLYOFFICE/onlyoffice.git", branch_name: str = None,
                 modules: str = "core desktop builder server mobile"):
        """
        Initialize GitOperations with branding configuration and configure repositories.
        
        Args:
            branding: Branding name (default: onlyoffice)
            base_branch: Base branch to work from (default: develop)
            branding_url: Relative path from git host base (default: ONLYOFFICE/onlyoffice.git)
            branch_name: Name of the branch to create (required for branch operations)
            modules: Modules to include (default: core desktop builder server mobile)
        """
        self.branding = branding
        self.base_branch = base_branch
        self.branding_url = branding_url
        self.branch_name = branch_name
        self.modules = modules
        self.work_dir = None
        
        # Configure repositories immediately
        self._configure()
        
        # Update repositories after configuration
        repositories = self.get_configured_repositories()
        #base.update_repositories(repositories)
    
    def create_branch(self, branch_name: str, repo_dir: str = None) -> bool:
        """
        Create a new branch using base.cmd_in_dir.
        
        Args:
            branch_name: Name of the new branch
            repo_dir: Repository directory (optional, uses current if not specified)
            from_branch: Branch to create from (optional, uses current if not specified)
        
        Returns:
            bool: True if successful, False otherwise
        """
        work_dir = repo_dir or self.work_dir
        logger.info(f"Creating branch '{branch_name}' in {work_dir}")
        
        try:
            # Create and checkout new branch
            base.cmd_in_dir(work_dir, "git", ["checkout", "-b", branch_name], True)
            logger.info(f"Successfully created branch: {branch_name}")
            return True
        except SystemExit:
            logger.error(f"Failed to create branch: {branch_name}")
            return False
    
    def push_branch(self, branch_name: str, repo_dir: str = None, set_upstream: bool = True) -> bool:
        """
        Push a branch to remote repository using base.cmd_in_dir.
        
        Args:
            branch_name: Name of the branch to push
            repo_dir: Repository directory (optional, uses current if not specified)
            set_upstream: Whether to set upstream tracking (default: True)
        
        Returns:
            bool: True if successful, False otherwise
        """
        work_dir = repo_dir or self.work_dir
        logger.info(f"Pushing branch '{branch_name}' in {work_dir}")
        
        try:
            if set_upstream:
                # Push branch and set upstream tracking
                base.cmd_in_dir(work_dir, "git", ["push", "-u", "origin", branch_name], True)
            else:
                # Just push the branch
                base.cmd_in_dir(work_dir, "git", ["push", "origin", branch_name], True)
            
            logger.info(f"Successfully pushed branch: {branch_name}")
            return True
        except SystemExit:
            logger.error(f"Failed to push branch: {branch_name}")
            return False
    
    def _configure(self) -> bool:
        """
        Configure repositories using existing configure.py pattern from release.py.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Configuring and cloning repositories for branch: {self.base_branch}")
        
        try:
            # Get build_tools origin and construct branding URL from git host base
            build_tools_origin = base.git_get_origin()
            # Extract git host base (everything up to the host)
            # For https://github.com/ORG/build_tools.git -> https://github.com/
            # For git@github.com:ORG/build_tools.git -> git@github.com:
            if '://' in build_tools_origin:  # HTTPS
                host_base = build_tools_origin.split('/', 3)[0] + '//' + build_tools_origin.split('/', 3)[2] + '/'
            else:  # SSH
                host_base = build_tools_origin.split(':', 1)[0] + ':'
            
            branding_url = host_base + self.branding_url
            
            logger.info(f"Build tools origin: {build_tools_origin}")
            logger.info(f"Git host base: {host_base}")
            logger.info(f"Using branding URL: {branding_url}")
            
            # Check platform and dependencies like in release.py
            platform = base.host_platform()
            if platform == "windows":
                dependence.check_pythonPath()
                dependence.check_gitPath()
            
            # Run configure.py like in release.py
            configure_args = [
                'configure.py',
                '--branding', self.branding,
                '--branding-url', branding_url,
                '--branch', self.base_branch,
                '--module', self.modules,
                '--update', '1',
                '--clean', '0'
            ]
            
            base.cmd_in_dir('../../', 'python', configure_args)
            
            # Parse configuration like in release.py
            config.parse()
            
            # Update build_tools repository
            base.git_update('build_tools')

            # Update branding repository
            base.git_update(self.branding)
            
            # Correct defaults (the branding repo is already updated)
            config.parse_defaults()
            
            logger.info("Successfully configured")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure and clone: {e}")
            return False
    
    def get_configured_repositories(self) -> Dict:
        """Get repositories using existing base.get_repositories() pattern from release.py."""
        repositories = base.get_repositories()
        repositories['core-ext'] = [True, False]
        repositories['build_tools'] = [True, False]
        repositories[self.branding] = [True, False]
        return repositories
    
    def _iterate_repositories(self, operation_func, operation_name: str) -> bool:
        """
        Iterate over all repositories and apply the given operation function.
        
        Args:
            operation_func: Function to apply to each repository (takes repo_name and repo_path)
            operation_name: Name of the operation for logging
        
        Returns:
            bool: True if at least one operation succeeded, False otherwise
        """
        repositories = self.get_configured_repositories()
        success_count = 0
        total_count = len(repositories)
        
        for repo_name in repositories:
            current_dir = repositories[repo_name][1]
            repo_path = f"../../../{repo_name}" if current_dir == False else current_dir
            
            if base.is_dir(repo_path):
                if operation_func(repo_name, repo_path):
                    success_count += 1
                else:
                    logger.warning(f"✗ Failed to {operation_name} in {repo_name}")
            else:
                logger.warning(f"Repository {repo_name} not found at {repo_path}")
        
        logger.info(f"{operation_name.capitalize()} completed in {success_count}/{total_count} repositories")
        return success_count > 0
    
    def delete_branch(self, branch_name: str, repo_dir: str = None, force: bool = False) -> bool:
        """
        Delete a branch using base.cmd_in_dir.
        
        Args:
            branch_name: Name of the branch to delete
            repo_dir: Repository directory (optional, uses current if not specified)
            force: Whether to force delete the branch (default: False)
        
        Returns:
            bool: True if successful, False otherwise
        """
        work_dir = repo_dir or self.work_dir
        logger.info(f"Deleting branch '{branch_name}' in {work_dir}")
        
        try:
            # Switch to base branch first to avoid deleting current branch
            base.cmd_in_dir(work_dir, "git", ["checkout", self.base_branch], True)
            
            # Delete local branch
            delete_flag = "-D" if force else "-d"
            base.cmd_in_dir(work_dir, "git", ["branch", delete_flag, branch_name], True)
            logger.info(f"Successfully deleted local branch: {branch_name}")
            
            # Delete remote branch
            try:
                base.cmd_in_dir(work_dir, "git", ["push", "origin", "--delete", branch_name], True)
                logger.info(f"Successfully deleted remote branch: {branch_name}")
            except SystemExit:
                logger.warning(f"Failed to delete remote branch: {branch_name} (may not exist)")
            
            return True
        except SystemExit:
            logger.error(f"Failed to delete branch: {branch_name}")
            return False

    def create_branches(self) -> bool:
        """
        Create a branch with the given name in all repositories.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Creating branch '{self.branch_name}' in all repositories")
        
        def create_and_push_branch(repo_name: str, repo_path: str) -> bool:
            """Create and push branch for a single repository."""
            if self.create_branch(self.branch_name, repo_path):
                logger.info(f"✓ Created branch '{self.branch_name}' in {repo_name}")
                # Push the created branch
                if self.push_branch(self.branch_name, repo_path):
                    logger.info(f"✓ Pushed branch '{self.branch_name}' in {repo_name}")
                    return True
                else:
                    logger.warning(f"✗ Failed to push branch '{self.branch_name}' in {repo_name}")
                    return False
            else:
                logger.warning(f"✗ Failed to create branch '{self.branch_name}' in {repo_name}")
                return False
        
        try:
            return self._iterate_repositories(create_and_push_branch, f"create and push branch '{self.branch_name}'")
        except Exception as e:
            logger.error(f"Failed to create branch in all repositories: {e}")
            return False

    def remove_branches(self, force: bool = False) -> bool:
        """
        Remove a branch with the given name from all repositories.
        
        Args:
            force: Whether to force delete the branch (default: False)
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Removing branch '{self.branch_name}' from all repositories")
        
        def delete_branch_operation(repo_name: str, repo_path: str) -> bool:
            """Delete branch for a single repository."""
            if self.delete_branch(self.branch_name, repo_path, force):
                logger.info(f"✓ Removed branch '{self.branch_name}' from {repo_name}")
                return True
            else:
                logger.warning(f"✗ Failed to remove branch '{self.branch_name}' from {repo_name}")
                return False
        
        try:
            return self._iterate_repositories(delete_branch_operation, f"remove branch '{self.branch_name}'")
        except Exception as e:
            logger.error(f"Failed to remove branch from all repositories: {e}")
            return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='Git Operations Tool - Create and Remove Branches')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create branch command (configure, clone and create branch in all repositories)
    branch_parser = subparsers.add_parser('create', help='Configure, clone and create branch in all repositories')
    branch_parser.add_argument('branch_name', help='Name of the branch to create')
    branch_parser.add_argument('--base-branch', default='develop', help='Base branch to work from (default: develop)')
    branch_parser.add_argument('--branding', default='onlyoffice', help='Branding name')
    branch_parser.add_argument('--branding-url', default='ONLYOFFICE/onlyoffice.git', help='Relative path from git host base (default: ONLYOFFICE/onlyoffice.git)')
    branch_parser.add_argument('--modules', default='core desktop builder server mobile', help='Modules to include')
    
    # Remove branch command (configure, clone and remove branch from all repositories)
    remove_parser = subparsers.add_parser('remove', help='Configure, clone and remove branch from all repositories')
    remove_parser.add_argument('branch_name', help='Name of the branch to remove')
    remove_parser.add_argument('--base-branch', default='develop', help='Base branch to work from (default: develop)')
    remove_parser.add_argument('--branding', default='onlyoffice', help='Branding name')
    remove_parser.add_argument('--branding-url', default='ONLYOFFICE/onlyoffice.git', help='Relative path from git host base (default: ONLYOFFICE/onlyoffice.git)')
    remove_parser.add_argument('--modules', default='core desktop builder server mobile', help='Modules to include')
    remove_parser.add_argument('--force', action='store_true', help='Force delete the branch (equivalent to git branch -D)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    git_ops = GitOperations(args.branding, args.base_branch, args.branding_url, args.branch_name, args.modules)
    
    if args.command == 'create':
        success = git_ops.create_branches()
        sys.exit(0 if success else 1)
    elif args.command == 'remove':
        success = git_ops.remove_branches(args.force)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
