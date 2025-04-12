from PIL import Image
import pytesseract


bill_text = pytesseract.image_to_string(Image.open('bill.jpg'))
class RestaurantBillSplitter:
    def __init__(self):
        self.menu_items = []
        self.people = []
        self.grand_total = 0
        self.tax = 0
        self.found_total = False

    def extract_items(self, ocr_text):
        """Extract items from bill text, stopping at totals"""
        lines = ocr_text.split('\n')
        currency_symbols = ('₹', '$', 'Rs', 'rs')
        total_keywords = ('total', 'amt', 'amount', 'balance', 'subtotal')
        
        for line in lines:
            if self.found_total:
                break
                
            line_lower = line.strip().lower()
            if any(keyword in line_lower for keyword in total_keywords):
                if any(symbol in line for symbol in currency_symbols):
                    self.process_total_line(line)
                    self.found_total = True
                continue
                
            if any(symbol in line for symbol in currency_symbols):
                self.process_item_line(line)

    def process_item_line(self, line):
        """Process a single menu item line"""
        for symbol in ('₹', '$', 'Rs', 'rs'):
            if symbol in line:
                price_part = line[line.find(symbol):]
                price_str = ''.join(c for c in price_part if c.isdigit() or c == '.')
                try:
                    price = float(price_str)
                    name = line[:line.find(symbol)].strip()
                    self.menu_items.append({
                        'name': name,
                        'price': price,
                        'consumers': []  # Track who ate this
                    })
                    break
                except ValueError:
                    continue

    def process_total_line(self, line):
        """Process the total/tax line"""
        for symbol in ('₹', '$', 'Rs', 'rs'):
            if symbol in line:
                price_part = line[line.find(symbol):]
                price_str = ''.join(c for c in price_part if c.isdigit() or c == '.')
                try:
                    amount = float(price_str)
                    if 'tax' in line.lower():
                        self.tax = amount
                    else:
                        self.grand_total = amount
                    break
                except ValueError:
                    continue

    def input_people(self):
        """Take input for number of people and their names"""
        num_people = int(input("Enter number of people: "))
        for i in range(num_people):
            name = input(f"Enter name of person {i+1}: ").strip()
            self.people.append({
                'name': name,
                'share': 0,
                'items': []
            })

    def select_items_for_people(self):
        """Let each person select items they ate"""
        for person in self.people:
            print(f"\n{person['name']}, select items you ate (comma separated numbers):")
            self.show_menu()
            choices = input("Your choices: ").strip().split(',')
            
            for choice in choices:
                try:
                    index = int(choice.strip()) - 1
                    if 0 <= index < len(self.menu_items):
                        # Add to person's items
                        person['items'].append(self.menu_items[index])
                        # Add to item's consumers
                        if person['name'] not in self.menu_items[index]['consumers']:
                            self.menu_items[index]['consumers'].append(person['name'])
                except ValueError:
                    continue

    def show_menu(self):
        """Display the extracted menu"""
        print("\nAvailable Items:")
        for i, item in enumerate(self.menu_items, 1):
            print(f"{i}. {item['name']} - {item['price']:.2f}")

    def calculate_shares(self):
        """Calculate each person's share including tax"""
        if not self.grand_total:
            self.grand_total = sum(item['price'] for item in self.menu_items)
            if self.tax:
                self.grand_total += self.tax
        
        # Reset shares
        for person in self.people:
            person['share'] = 0
        
        # Calculate food shares
        for item in self.menu_items:
            if item['consumers']:
                share_per_person = item['price'] / len(item['consumers'])
                for consumer in item['consumers']:
                    for person in self.people:
                        if person['name'] == consumer:
                            person['share'] += share_per_person
        
        # Add tax proportionally
        if self.tax:
            total_food_share = sum(person['share'] for person in self.people)
            if total_food_share > 0:  # Avoid division by zero
                for person in self.people:
                    tax_share = (person['share']/total_food_share) * self.tax
                    person['share'] += tax_share

    def show_summary(self):
        """Show the final bill summary"""
        self.calculate_shares()
        
        print("\n=== FINAL BILL SUMMARY ===")
        print(f"Grand Total: {self.grand_total:.2f}")
        if self.tax:
            print(f"(Includes tax: {self.tax:.2f})")
        
        print("\nItems Breakdown:")
        for item in self.menu_items:
            consumers = ', '.join(item['consumers']) if item['consumers'] else 'Not consumed'
            print(f"- {item['name']} ({item['price']:.2f}): {consumers}")
        
        print("\nIndividual Shares:")
        for person in sorted(self.people, key=lambda x: x['name']):
            print(f"{person['name']}: {person['share']:.2f} ({(person['share']/self.grand_total)*100:.1f}%)")

# Example Usage
if __name__ == "__main__":
    splitter = RestaurantBillSplitter()
    
    # Step 1: Extract items from bill
    splitter.extract_items(bill_text)
    
    # Step 2: Input people
    splitter.input_people()
    
    # Step 3: Let people select items
    splitter.select_items_for_people()
    
    # Step 4: Show final split
    splitter.show_summary()