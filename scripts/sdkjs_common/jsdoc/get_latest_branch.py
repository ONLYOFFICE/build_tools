import subprocess

def fetch_branches():
    #Fetch all branches without tags from the remote.
    subprocess.run(['git', 'fetch', '--no-tags', 'origin', '+refs/heads/*:refs/remotes/origin/*'], check=True)

def get_branches():
    #Get list of branches in the repository."""
    result = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True)
    return [line.strip() for line in result.stdout.splitlines()]

def parse_version(version_str):
    #Parse version string and return a tuple of integers (major, minor, patch).
    try:
        return tuple(map(int, version_str.lstrip('v').split('.')))
    except ValueError:
        return (0, 0, 0)  # Default for non-parsable versions

def get_max_version_branch(branches):
    #Find the branch with the highest version.
    max_branch = None
    max_version = (0, 0, 0)

    for branch in branches:
        parts = branch.split('/')
        if len(parts) >= 2 and (parts[1] == 'hotfix' or parts[1] == 'release'):
            version = parse_version(parts[2])
            if version > max_version:
                max_version = version
                max_branch = parts

    return max_branch

if __name__ == "__main__":
    fetch_branches()  # Fetch branches without tags
    branches = get_branches()
    max_version_branch = get_max_version_branch(branches)
    if max_version_branch:
        print('/'.join(max_version_branch[1:]))  # Print only the branch name without origin
