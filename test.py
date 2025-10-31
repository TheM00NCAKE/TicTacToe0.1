import copernicusmarine

copernicusmarine.subset(
  dataset_id="dataset-armor-3d-rep-monthly",
  variables=["mlotst", "so", "to", "ugo", "vgo", "zo"],
  minimum_longitude=-179.875,
  maximum_longitude=179.875,
  minimum_latitude=-82.125,
  maximum_latitude=89.875,
  start_datetime="2022-12-01T00:00:00",
  end_datetime="2022-12-01T00:00:00",
  minimum_depth=0,
  maximum_depth=0,
)