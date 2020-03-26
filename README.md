# build_tools

## How to use

### Using docker

```bash
mkdir out
docker build --tag onlyoffice-document-editors-builder .
docker run -v $PWD/out:/build_tools/out onlyoffice-document-editors-builder
```

Result will be at `./out` directory
