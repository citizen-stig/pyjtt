

#build_mac:
#	pipenv

generate_widgets:
	pipenv run pyuic6 -x pyjtt/resources/main_window.ui -o pyjtt/widgets/main_window.py
	pipenv run pyuic6 -x pyjtt/resources/login_screen.ui -o pyjtt/widgets/login_window.py
	pipenv run pyuic6 -x pyjtt/resources/worklog_window.ui -o pyjtt/widgets/worklog_window.py

run:
	pipenv run python pyjtt/app.py
