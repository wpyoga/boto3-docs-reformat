all:

rerun:
	git show master:boto3-html-reformat.py > boto3-html-reformat.py
	for file in html/reference/services.orig/*.html; do \
		echo $$file; \
		cat "$$file" | python3 boto3-html-reformat.py > html/reference/services/"$$(basename "$$file")"; \
	done
	@echo Rerun done. You can run 'git commit html -m "docs: rerun"' to commit the changes to git.

