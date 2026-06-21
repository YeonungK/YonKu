with open('GUI/ExperimentSettingUi.py', 'r') as f:
    content = f.read()

# Find and remove commented class
idx = content.find('# class ExperimentSettingUi')
if idx > 0:
    content = content[:idx].rstrip()

with open('GUI/ExperimentSettingUi.py', 'w') as f:
    f.write(content)

print('Cleaned ExperimentSettingUi.py')
