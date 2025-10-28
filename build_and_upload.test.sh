printf "Removing previous build folder"
rm -rf ./dist
printf "Building..."
python -m build
printf "Uploading to TEST with twine"
twine upload --repository testpypi dist/*

