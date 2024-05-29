import inquirer
import llm
import openapi
import pandas as pd
import json

# Load the data
apps_df = pd.read_json(path_or_buf="apps.jsonl", lines=True)
apps_df = apps_df.drop(columns=['link'])
apps_df = apps_df.rename(columns={'h2': 'action', 'p': 'description'})
apps_df = apps_df.groupby('name')
apps_dict = {name: group.drop('name', axis=1).to_dict('records') for name, group in apps_df}
# apps_list = apps_df.T.to_dict().values()

def read_integration_from_user():
    questions = [
        inquirer.Text('integration', message="Enter an integration from Zapier"),
    ]
    answers = inquirer.prompt(questions)
    assert answers is not None
    generate_new_integration(answers['integration'])

def explore_integrations():
    # let the user scroll through all of the Zapier integrations
    
    # both generate_new_integration and explore_integrations() should lead into the next block
    # which is choosing the generation part and the language
    questions = [
        inquirer.List('integration',
            message="Choose an integration from Zapier",
            choices=list(apps_dict.keys()),
        ),
    ]
    answers = inquirer.prompt(questions)
    assert answers is not None
    generate_new_integration(answers['integration'])

def generate_new_integration(api_name):
    print(api_name)
    print('generating')
    questions = [
        inquirer.List('action',
            message="Choose an action from Zapier",
            choices=list(apps_dict[api_name]),
        ),
        inquirer.List('type',
            message="Choose type of generation",
            choices=['Zero-shot', 'Few-shot'],
        ),
        inquirer.Text('language', message='Choose your programming language of choice'),
    ]
    answers = inquirer.prompt(questions)
    assert answers is not None

    match answers['type']:
        case 'Zero-shot':
            print(f'Generating a {answers['language']} script using zero-shot learning...')
            generated = llm.generate_zero_shot(answers['action']['action'], answers['action']['description'], api_name, answers['language'])
           
        case 'Few-shot':
            print(f'Generating a {answers['language']} script using few-shot learning...')
            # print(llm.generate_few_shot(answers['action']['action'], answers['action']['description'], api_name, answers['language']))
            generated = llm.generate_few_shot(answers['action']['action'], answers['action']['description'], api_name, answers['language'])
    assert generated is not None
    parsed = json.loads(generated)

    print('Script successfully generated!')
    print('\n\nHow to use it:')
    print(parsed['explanation'])

    # save the script as a file
    with open('./generated/' + parsed['filename'], 'w+') as script:
        # Writing data to a file
        script.write(parsed['code'])

    print(f'\nYou can find the script here: {parsed['filename']}')


def check_openapi():
    questions = [
        inquirer.Text('api', message="Choose any API"),
    ]
    answers = inquirer.prompt(questions)
    assert answers is not None

    # get a Zapier integration from the user
    # check whether an OpenAPI spec exists
    # return the link to the OpenAPI spec
    print(openapi.search(answers['api']))

questions = [
    inquirer.List('query',
                message="What do you want to do?",
                choices=['Generate integration based on Zapier', 'Explore existing Zapier integrations', 'Check if OpenAPI spec is available'],
            ),
]

answers = inquirer.prompt(questions)
assert answers is not None

match answers['query']:
    case 'Generate integration based on Zapier':
        read_integration_from_user()
    case 'Explore existing Zapier integrations':
        explore_integrations()
    case 'Check if OpenAPI spec is available':
        check_openapi()
