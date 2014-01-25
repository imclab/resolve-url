##REQUIREMENTS

[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)

###DEVELOPMENT

    # Clone secrets and fablib repositories
    git clone git@github.com:NUKnightLab/secrets.git
    git clone git@github.com:NUKnightLab/fablib.git
    
    # Change into project directory
    cd resolve-url
    
    # Make virtual environment
    mkvirtualenv resolve-url
    
    # Activate virtual environment
    workon resolve-url
    
    # Install requirements
    pip install -r requirements.txt
    
    # Setup (if necessary)
    fab loc setup

    # Start the development server
    python api.py
    

###DEPLOYMENT

Projects are deployed to the application user's home directory in: ``/home/apps/sites``

Deployment is by direct clone from git. The name of the git repository will be the name of the directory in ``sites`` that is created by the ``git clone`` command.

    # Do this once before the intial deployment (replace `stg` with `prd` for production)
    fab stg setup
    
    # Do this to deploy (replace `stg` with `prd` for production)
    fab stg deploy


###REQUIRED ENVIRONMENT VARIABLES:

- FLASK_SETTINGS_MODULE
- WORKON_HOME (set manually if not using mkvirtualenv)


