This is an AWS Lambda function that analyzes PDFs to see if the text follows <a href="https://en.wikipedia.org/wiki/Benford%27s_law">Benford’s Law</a>, a common method for detecting fraud in numeric data.

To use it, you must fill in the `credentials.txt` file with the desired AWS bucket, region, and access keys before running the Lambda function.

When called, the Lambda function does the following:
1. Downloads the given PDF 
2. Opens the PDF, extracts the text from each page, and tallies all numeric values based on first significant digit
3. Counts the # of values that start with 1, 2, 3, ..., 9. Values that consist entirely of 0’s are not counted.
4. Outputs results to the console *and* to a file with same base filename as the PDF but with .txt extension
5. Uploads the .txt file to the same S3 bucket