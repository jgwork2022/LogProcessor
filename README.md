# LogProcessor
Log processing exercise.


Build image with:

docker build -t log_processor .

Run with: (ex: Windows)

docker run -v <path_to_project>\test:/test log_processor -h

docker run -v <path_to_project>\test:/test log_processor -mltev -o /test/output/output.json /test/input


