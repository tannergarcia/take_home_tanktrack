# Technical notes

Live deployment [link](https://tanktracktakehome-beta.vercel.app/)

## Design
- Used Python with Flask for core logic and API, based on familarity.
- SQLAlchemy for ORM, making interaction with DB way cleaner and easier
- Since assumption is no time zones, all times are saved as minutes past midnight, easing overlap calculations
- Recurring jobs are first expanded and validated before attempting to insert any of them
    - These are linked together with a series ID to allow for series-level modifications in the future
- Automatically generates seed data relative to current week
- Frotnend is basic, uses React, everything is connected over Flask API, no auth
- Automatic tests for core logic and API handling using PyTest

## Known Limitations
- Events created as a series are marked as "Week 1 of x". No handling in the case of an event in the series being deleted, the number is just skipped
- Vercel deployment DB is not persistant, reseeds every time application is relaunched, which is very often. Most likely due to misconfiguration

## Use of AI
- Claude was used to create an in depth plan based on the provided instructions. I provided it specific design choices (Python, React, structure of data).
- This plan was then fed into CoPilot in VS Code and the agent was instructed to build step by step.
- As each step was completed, I reviewed the code and made any changes I deemed necessary.
- Once the core application was built, I performed testing of the frontend, where I have the least experience. I instructed the AI to fix various visual bugs or incorrect uses of the API