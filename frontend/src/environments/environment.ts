export const environment = {
    production: false,
    apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
    auth0: {
        url: 'sw-ark.eu', // the auth0 domain prefix
        audience: 'coffee-shop-api-id', // the audience set for the auth0 app
        clientId: 'VcK9n05N1xr3Xp4rIegx5Uc1bIM2j5EW', // the client id generated for the auth0 app
        callbackURL: 'http://localhost:4200', // the base url of the running ionic application.
    }
};
