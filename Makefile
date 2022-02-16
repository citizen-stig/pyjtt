

build_mac:
	pipenv run python setup.py bdist_dmg

generate_widgets:
	pipenv run pyuic6 -x resources/main_window.ui -o pyjtt/widgets/main_window.py
	pipenv run pyuic6 -x resources/login_screen.ui -o pyjtt/widgets/login_window.py
	pipenv run pyuic6 -x resources/worklog_window.ui -o pyjtt/widgets/worklog_window.py

run:
	pipenv run python pyjtt/app.py
