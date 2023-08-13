import nltk
nltk.download('punkt')

# from langchain.document_loaders import JSONLoader
# import json
# file_path = 'doaj/a.json'

# with open(file_path, 'r') as file:
#     data = json.load(file)

# # Filter the objects that have a .bibjson.abstract property
# filtered_data = [item for item in data if 'year' in item["bibjson"] and 'abstract' in item['bibjson']]

# # Write the filtered data back to the file
# with open(file_path, 'w') as file:
#     json.dump(filtered_data, file, indent=4)

# # # Read the JSON file
# # with open(file_path, 'r') as file:
# #     data = json.load(file)

# # print(data[102]["bibjson"]["title"])

# # formatted_data = []

# # for i, item in enumerate(data):
# #     print(item["bibjson"]["title"])
# #     if "abstract" in item["bibjson"]:
# #         formatted_data.append(item)

# # print(len(formatted_data))


# # def metadata_func(record: dict, metadata: dict) -> dict:
# #     metadata["journal"] = record["journal"]["title"]
# #     metadata["publisher"] = record["journal"]["publisher"]
# #     if "keywords" in record:
# #         metadata["keywords"] = "; ".join(record["keywords"])
# #     metadata["year"] = int(record["year"])
# #     metadata["author"] = "; ".join([author["name"] for author in record["author"]])
# #     metadata["url"] = record["link"][0]["url"]
# #     metadata["title"] = record["title"]
# #     return metadata


# # tingy = JSONLoader(
# #     file_path="doaj/a.json",
# #     jq_schema=".[].bibjson",
# #     content_key="abstract",
# #     metadata_func=metadata_func,
# # ).load()[:100]


# # print(tingy[0])
