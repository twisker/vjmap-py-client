# vjmap-py-client

Python Client for VjMap REST services

## Installation

Install with pip:

```bash
pip install vjmap-py-client
```

## Usage

```python
from vjmap_py_client import VjmapClient, RectQueryParameter, PointQueryParameter, ExprQueryParameter, ConditionQueryParameter

client = VjmapClient(access_token="your_access_token", base_url="your_base_url")

# Upload a map
upload_result = client.upload_map(map_file_path="your_map_file_path")
map_id = upload_result["mapid"]
fileid = upload_result["fileid"]
uploadname = upload_result["uploadname"]

# Open a map
result = client.open_map(map_id=map_id,
                         params={"fileid": fileid, "uploadname": uploadname})
version = result["version"]

# List all maps
result = client.list_maps(map_id=map_id, version=version)

# Get bounds
result = client.get_data_bounds(map_id=map_id, version=version)
x1, y1, x2, y2 = result["bounds"]

# Query a map
rect = RectQueryParameter(x1=x1, y1=y1, x2=x2, y2=y2)
# you can also use PointQueryParameter or ExprQueryParameter or ConditionQueryParameter
result = client.query_features(map_id=map_id, version=version, parameters=rect)

# Get metadata
result = client.get_metadata(map_id=map_id, version=version)

# Close a map
result = client.close_map(map_id=map_id, version=version)

```