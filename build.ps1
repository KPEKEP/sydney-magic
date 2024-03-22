rm ./dist -r -force
python ./setup.py sdist bdist_wheel
twine check ./dist/*
twine upload ./dist/*