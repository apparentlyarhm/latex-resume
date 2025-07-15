Latex code for my resume.

If the latex compiler is installed correctly, no file other than the `.tex` is required. 

ive also added a minimal Python script to upload the generated file to a public Google Drive file, replacing the existing file without breaking its link. Uses a service account and auto-includes a timestamp in the file name.

## Getting started (for the script)

1. Install uv (see [here](https://docs.astral.sh/uv/getting-started/installation/))

2. We  will keep it simple. just use uv's `pip` layer

```bash
uv pip install -r req.txt
```
3. Make sure to create an env similar to `.env.example`. You need service account credenentials (in JSON) and your `file-id` (see below)

4. Done! just run:

```bash
python main.py
```

## Getting the file ID and my thoughts

As of writing this, a typical shared google drive link looks like:

`
https://drive.google.com/file/d/<file-id>/view?usp=drive_link
`

that id is what this script needs.

Well there are many possible ways a drive link can function and we could do something like

```python
patterns = [
        r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",     # /file/d/<id>/
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",   # /open?id=<id>
        r"drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)",     # /uc?id=<id>
    ]
```
and use regex to pattern match, which is brittle in my opinion. (what if they change the format)

however since the api client uses the drive API (see [here](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update)) it is much less likely that they will change the parameter `file-id` format in this. So its better that we keep the script as is.