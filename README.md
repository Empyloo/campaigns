# campaigns
Campaigns function

## Run the cloud function locally

- Export the environment variables in the terminal

```bash
export PROJECT_ID=''
export REGION=''
export SURVEY_EXECUTOR_FUNCTION_URL=''
export SERVICE_ACCOUNT=''
export SUPABASE_SERVICE_ROLE_SECRET_ID=''
export QUEUE_NAME=''
export VERSION_ID=''

export SUPABASE_URL=''
export SUPABASE_ANON_KEY=''
```

- Run the function

```bash
functions-framework --target=main --port=8080 --debug
```