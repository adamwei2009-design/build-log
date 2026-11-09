# Examples

Small, working Python examples of ideas from my build log. They are fresh code written to show the idea, not copies of anything from work. All data is made up.

| File | The idea | Build log |
|---|---|---|
| `merge_repeats.py` | Several messages from one sender within 30 minutes become one alert. A follow-up only raises an UPDATE if it adds new urgent words. | Repeat emails merged into one alert |
| `route_by_booking.py` | A refund or invoice question goes to the team doing the customer's job if it's booked in the next 7 days, with accounts copied in. Otherwise it goes to accounts. | Context beats category |
| `safe_delete_gate.py` | A delete is only allowed when every file is in the backup with the same name and size. One missing file blocks the lot. | Safe delete gate |
| `strip_png_metadata.py` | Removes hidden metadata chunks (such as content credentials) from a PNG without changing a single pixel. | Used on every card I post |

## Run them

```
python merge_repeats.py
python route_by_booking.py
python safe_delete_gate.py
python strip_png_metadata.py in.png out.png
```

## Tests

```
pip install pytest
pytest -q
```

10 tests, all passing. They cover the edge cases I care about: the 30-minute window is measured from the last message, the same sender with different capitals counts as one, an empty delete list is refused, and stripped PNGs keep the exact same image.
