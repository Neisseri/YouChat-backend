coverage run --source st_im_django,User,utils,Session,WebSocket,constants,CSRF -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
coverage xml -o coverage-reports/coverage.xml
coverage report
exit $ret