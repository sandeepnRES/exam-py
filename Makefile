paperzip:
	zip -r paper.zip paper -x "paper/*/*_results/*" -x "paper/**/.DS_Store" -x "paper/.DS_Store"

start:
	APP_PORT=8000 python server.py