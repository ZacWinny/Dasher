import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

# Parse the XML file
tree = ET.parse('report\coverage.xml')
root = tree.getroot()

# Get the total lines and covered lines
total_lines = int(root.get('lines-valid'))
covered_lines = int(root.get('lines-covered'))

# Calculate the uncovered lines
uncovered_lines = total_lines - covered_lines

# Create a pie chart
labels = 'Covered Lines', 'Uncovered Lines'
sizes = [covered_lines, uncovered_lines]
colors = ['green', 'red']  # Specify colors
explode = (0.1, 0)  # "explode" the 1st slice

plt.figure(figsize=(10, 5), dpi=500)  # Create a new figure
plt.subplot(1, 2, 1)  # Add a subplot to the figure (1 row, 2 columns, 1st plot)
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Code Coverage')  # Add a title
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.legend(coverage_rates, title='Coverage Rate', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))  # Add a legend

# Get the coverage rate for each package
packages = [package.get('name') for package in root.findall('.//package')]
coverage_rates = [float(package.get('line-rate')) for package in root.findall('.//package')]

# # Create a bar chart
# plt.subplot(1, 2, 2)  # Add a subplot to the figure (1 row, 2 columns, 2nd plot)
# plt.bar(packages, coverage_rates)
# plt.xlabel('Package')
# plt.ylabel('Coverage Rate')
# plt.title('Package Coverage Rates')
# plt.xticks(rotation=90)  # Rotate the x-axis labels for better readability

plt.tight_layout()  # Adjust the layout so that the plots do not overlap
plt.show()