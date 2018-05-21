from setuptools import setup

setup(
    name="Dreamer",
    version='0.11',
    description='Simple messenger.',
    long_description='Hanita is simple messenger with multiusers chats.',
    url='https://github.com/SergioWolf/dreamer',
    license='MIT',
    keywords=['python', 'messenger', 'dreamer'],
    author='Sergey Volkov',
    author_email='sergio_volf@mail.ru',
    packages=[
        'dreamer_client',
        'dreamer_client/jim',
        'dreamer_server',
        'dreamer_server/avatars',
        'dreamer_server/jim',
        'dreamer_server/repo',
    ],
    package_data={
        '': ['default_avatar.png'],
    },
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'PyQt5==5.10.1',
        'SQLAlchemy==1.2.7',
        'Jinja2==2.10',
        'Pillow==5.1.0',
        'PyOpenGL==3.1.0',
    ],
)
