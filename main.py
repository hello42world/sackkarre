import boto3
import probe_state_repo


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    ddb = boto3.resource('dynamodb',
                         endpoint_url='http://localhost:8000',
                         region_name='us-west-2')
    p = probe_state_repo.ProbeStateRepo(ddb)
    #p.update_probe_with_success('foo', str(1.33))
    #p.update_probe_with_success('bar', str(22.42))
    p.update_probe_with_failure('zoo', 'boom!')
    #p.update_probe_with_success('zoo', str(5))

    p.dump()

    # probe_spec.load('spec.yaml')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
