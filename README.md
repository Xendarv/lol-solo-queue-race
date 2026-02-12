# LoL Ranked Tracker

Small side project to track my friends’ Solo Queue progress in League of Legends.  
The goal is just to see how everyone’s climbing over time — nothing fancy or official.

The script pulls data from the Riot Games API, converts rank + LP into a rough numeric score, stores it in an Excel file, and makes a simple chart so I can quickly compare progress.

## How it works

- Fetches ranked data for a fixed list of summoners
- Converts ranks and divisions into a numeric score
- Stores snapshots in `ranked_progress.xlsx`
- Generates a line chart `ranked_progress.png` showing progression

This is just for fun, mostly for myself and a few friends. GM+ ranks are approximate, and the focus is readability, not correctness.

## License

MIT License
