# DocSlice OpenAPI and Postman collection

Try the [DocSlice](https://docslice.app) API without writing code, or generate a client in your language.

| File | Use it for |
|---|---|
| [`openapi.json`](openapi.json) | OpenAPI 3.1 description of the public API: import it in Insomnia, Bruno, Hoppscotch, or generate a client with [OpenAPI Generator](https://openapi-generator.tech/) |
| [`docslice.postman_collection.json`](docslice.postman_collection.json) | Postman collection (v2.1), ready to run |

## Postman in one minute

1. Create a free account at **https://api.docslice.app/app#signup** and an API key in the dashboard
   (500 welcome pages + 50 pages a month, no credit card).
2. In Postman: **Import** → pick `docslice.postman_collection.json` (or paste the raw GitHub URL of the file).
3. Open the collection → **Variables** → paste your key in `apiKey` (current value). Every request uses it as a Bearer token.
4. Open the first request in **Document Conversion**, choose a file in the `file` field of the body and **Send**.
   The `schema` field already holds a small JSON Schema (invoice number, date, total): untick it to get the whole document.

## Generate a client

```bash
npx @openapitools/openapi-generator-cli generate -i openapi.json -g python -o docslice-client
```

Uploads are `multipart/form-data`; the JSON Schema for field extraction travels as a string in the `schema` field.

## What is in it

`GET /health`, `POST /v1/convert`, `POST /v1/convert/batch`, `GET /v1/jobs`, `GET /v1/jobs/{job_id}`,
`GET /v1/usage`, `GET /v1/usage/history`, and the API key endpoints. Guides and examples:
[docslice.app/docs](https://docslice.app/docs/) · code in four languages: [docslice-examples](https://github.com/docslice/docslice-examples).

## Keep it current

`openapi.json` is exported from the DocSlice API; `python build_postman.py` rebuilds the collection from it.

MIT License.
