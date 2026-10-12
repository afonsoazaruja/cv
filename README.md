# cv

My CV, served at [cv.afonsoazaruja.com](https://cv.afonsoazaruja.com).

Everything comes from `cv.yaml`:

- **PDF** — [RenderCV](https://github.com/rendercv/rendercv) (Typst), one page, single column.
- **Web page** — `build_html.py` fills `template.html`; plain HTML/CSS, no JavaScript, with schema.org `Person` data.

```sh
./build.sh    # builds dist/ (needs uv)
./deploy.sh   # builds and rsyncs dist/ to the VPS (ssh host "site")
```

The server is the same Caddy VPS as the personal site, with this block in `/etc/caddy/Caddyfile`:

```
cv.afonsoazaruja.com {
    root * /var/www/cv.afonsoazaruja.com
    file_server
}
```
