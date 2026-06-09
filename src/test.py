
import tomlrt

if __name__=="__main__":

    with open("pyproject.toml", "rb") as f:
     doc = tomlrt.load(f)

    print(doc.get("_MASK_TO_STRFTIME"))
    # doc["project"]["version"] = "0.2.0"
    # doc["project"]["dependencies"].append("requests>=2")

    # print(tomlrt.dumps(doc)) 