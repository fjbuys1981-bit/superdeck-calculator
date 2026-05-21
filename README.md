# Preston Hire NZ SuperDeck Calculator

Streamlit MVP for selecting a SuperDeck platform configuration, checking applied load against SWL, reviewing reactions/deflections, viewing an indicative platform diagram, and exporting project data.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

1. Push this folder to a GitHub repository.
2. In Streamlit Cloud, create a new app from the repository.
3. Set the main file path to `app.py`.
4. Deploy.

## Current Features

- SuperDeck 2.2, 3.2, and 4.2 reference table from the MVP input
- 2 Prop, 4 Prop, and Boltdown options where data is available
- Worker, material, and additional load inputs
- PASS / WARNING / OVERLOADED status logic
- Load summary and engineering output tables
- Utilisation chart with 80% planning threshold
- Indicative platform, prop, slab edge, and load-zone visual
- Adjustable prop height/capacity check from the supplied prop drawings
- Project JSON, calculation CSV, and HTML report download

## Engineering Note

This MVP uses embedded reference values and simple SWL utilisation checks. It is intended for planning support and should be reviewed by a suitably qualified engineer before being used for temporary works decisions.
