from bcpandas import SqlCreds, to_sql


def dataframe_to_sql_bcpandas(
    engine,
    dataframe,
    table_name,
    dtype=None,
    schema="dbo",
    if_exists="replace",
    index=False,
):
    """
    A wrapper around bcpandas to_sql which is a wrapper around pandas DataFrame.to_sql

    Args:
        engine : sqlalchemy engine
        dataframe: pandas DataFrame
        table_name: table name to save as
        dtype (optional): data types to save as
        schema (optional): schema to save under
        if_exists (optional): fail/replace/append
        index (optional): Write DataFrame index as a column. Uses the index name as the column name in the table.
    """
    creds = SqlCreds.from_engine(engine)
    to_sql(
        df=dataframe,
        table_name=table_name,
        creds=creds,
        dtype=dtype,
        schema=schema,
        if_exists=if_exists,
        index=index,
    )
