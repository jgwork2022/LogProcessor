# LogProcessor
Log processing exercise.


Build image with:

docker build -t log_processor .

Run with: (ex: Windows)

docker run -v <path_to_project>\test:/test log_processor -h

docker run -v <path_to_project>\test:/test log_processor -mltev -o /test/output/output.json /test/input

Data from SecRepo website https://www.secrepo.com/#about published under a Creative Commons Attribution 4.0
International License


