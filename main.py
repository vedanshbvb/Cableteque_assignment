from bicycle_generator import generate_bicycles_stream
import json

def sanitize_unicode(obj):
    """
    Ensures all values in the dictionary have properly decoded characters.
    """
    if isinstance(obj, dict):
        return {k: sanitize_unicode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_unicode(i) for i in obj]
    elif isinstance(obj, str):
        return obj.replace("\u00b0", "°").replace("\u2033", "″").replace('\\"', '"')
    else:
        return obj

if __name__ == "__main__":
    path = input("Enter absolute path to Bicycle.xlsx: ").strip()
    output_path = "bicycles_output.json"
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[")
        first = True
        for bike in generate_bicycles_stream(path):
            bike = sanitize_unicode(bike)
            if not first:
                f.write(",\n")
            f.write(json.dumps(bike, indent=4, ensure_ascii=False))

            # if count < 1:
            print(json.dumps(bike, indent=4, ensure_ascii=False))  # Print all bikes

            print(count)

            first = False
            count += 1
        f.write("]\n")
    print(f"✅ Successfully generated {count} bicycle configurations.")

    # # Display one sample object from file
    # with open(output_path, encoding="utf-8") as f:
    #     bicycles = json.load(f)
    #     print("🔍 Sample object:")
    #     print(json.dumps(bicycles[0], indent=4, ensure_ascii=False))

    
    
    
    # /home/vedansh/Cableteque/Bicycle.xlsx
