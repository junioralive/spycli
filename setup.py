from setuptools import setup, find_packages

setup(
    name='spycli',
    version='1.0.1',
    author='junioralive',
    author_email='support@junioralive.in',
    description='A cli tool to browse and watch Movie/TV Shows/Anime/Kdrama/Cdráma/MORE',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/junioralive/spycli',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'pyfzf',
        'beautifulsoup4',
        'packaging',
    ],
    entry_points={
        'console_scripts': [
            'spycli=spycli.main:main',
            'spycli-md=spycli.utils.routes.moviesdrive.prompt:start_md',
            'spycli-anime=spycli.utils.routes.gogoanime.prompt:start_anime',
            'spycli-drama=spycli.utils.routes.dramacool.prompt:start_drama',
            'spycli-vidsrc=spycli.utils.routes.vidsrc.prompt:start_vidsrc',
            'spycli-flixhq=spycli.utils.routes.vidsrc.prompt:start_flixhq',
            'spycli.version=spycli.utils.core.version:get_version',
            'spycli.update=spycli.utils.core.update:check_for_updates',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
