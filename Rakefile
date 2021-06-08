# frozen_string_literal: true

desc 'Cleanup old build files'
task :clean do
  archive_name_pattern = 'build_tools*.tar.gz'
  sh('sudo rm -rf out')
  sh("rm #{archive_name_pattern}") unless Dir.glob(archive_name_pattern).empty?
end

desc 'Build version anew'
task build: :clean do
  sh('mkdir out')
  sh('docker build --tag onlyoffice-document-editors-builder .')
  sh("docker run -v #{Dir.pwd}/out:/build_tools/out onlyoffice-document-editors-builder")
end

desc 'Archive current build version'
task :archive do
  commit_hash = `git rev-parse --short HEAD`.strip
  branch = `git rev-parse --abbrev-ref HEAD`.gsub('/', '_').strip
  current_data = Time.now.strftime('%Y.%m.%d-%H.%M')
  archive_name = "build_tools-#{branch}-#{commit_hash}-#{current_data}.tar.gz"
  sh("tar -zcvf #{archive_name} out")
end
