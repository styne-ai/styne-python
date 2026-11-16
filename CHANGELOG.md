# Changelog

## 0.2.0 - 2026-11-16

- Regions: `Client(region="ams")` and `AsyncClient(region="ams")`, or `STYNE_REGION`, pick `https://<region>.api.styne.ai`. Regions are `ash` (US East) and
  `ams` (Europe); `us-east`, `ashburn`, `eu` and `eu-central` are accepted too. The chosen region is also the region of every browser and VM create that
  names none (a create from a snapshot keeps the snapshot's region). `base_url` and `STYNE_BASE_URL` take precedence.
- The default API host is now `ash.api.styne.ai` (it was `api.styne.ai`).
- `Browser.with_reconnect` and `AsyncBrowser.with_reconnect`: connect again and run your function again after the CDP socket closes.
  `styne.is_disconnect` is the classifier; pass your own as `is_disconnect=`.
- A rejected base URL no longer appears in full in the error message.

## 0.1.1

- Author and licence metadata (Apache-2.0).

## 0.1.0

- First release: VMs, files, ports, checkpoints, snapshots, cloud browsers; sync and async clients.
