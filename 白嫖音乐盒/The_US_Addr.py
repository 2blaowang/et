import random

def generate_tax_free_addresses():
    """
    生成所有美国免税州的邮寄地址。
    
    返回:
        list: 包含所有免税州地址信息的列表。
    """
    # 免税州列表
    tax_free_states = [
        "Alaska",
        "Delaware",
        "Montana",
        "New Hampshire",
        "Oregon"
    ]
    
    addresses = []
    
    # 生成每个免税州的具体地址信息
    for state in tax_free_states:
        if state == "Alaska":
            address = "123 Main St"
            city = "Anchorage"
            zip_code = "99501"
            phone = "907-555-1234"
        elif state == "Delaware":
            address = "456 Elm St"
            city = "Wilmington"
            zip_code = "19801"
            phone = "302-555-1234"
        elif state == "Montana":
            address = "789 Oak St"
            city = "Billings"
            zip_code = "59101"
            phone = "406-555-1234"
        elif state == "New Hampshire":
            address = "101 Pine St"
            city = "Concord"
            zip_code = "03301"
            phone = "603-555-1234"
        elif state == "Oregon":
            address = "202 Maple St"
            city = "Portland"
            zip_code = "97201"
            phone = "503-555-1234"
        
        # 将地址信息添加到列表中
        addresses.append({
            "地址": address,
            "城市": city,
            "州": state,
            "邮编": zip_code,
            "电话": phone
        })
    
    return addresses

def main():
    # 生成所有免税州的邮寄地址
    addresses = generate_tax_free_addresses()
    
    # 打印生成的地址信息
    for address_info in addresses:
        print(f"地址: {address_info['地址']}")
        print(f"城市: {address_info['城市']}")
        print(f"州: {address_info['州']}")
        print(f"邮编: {address_info['邮编']}")
        print(f"电话: {address_info['电话']}")
        print("-" * 30)

if __name__ == "__main__":
    main()