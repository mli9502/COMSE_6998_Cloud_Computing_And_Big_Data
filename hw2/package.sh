rm -rf index-photos-lf1 && mkdir index-photos-lf1

cp index-photos-lf1.py index-photos-lf1/lambda_function.py

cd index-photos-lf1
pip install --target ./package requests-aws4auth opensearch-py

cd package
zip -r ../index-photos-lf1.zip .

cd ..
zip index-photos-lf1.zip lambda_function.py
