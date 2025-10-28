printf "Removing previous build folder"
rm -rf ./dist
printf "Building..."
python -m build
printf "Uploading to PROD with twine"
twine upload --repository pypi dist/*

