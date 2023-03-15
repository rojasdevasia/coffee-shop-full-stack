
export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-i20z2y54qtc46c2h.us', // the auth0 domain prefix
    audience: 'coffeeshop', // the audience set for the auth0 app
    clientId: 'JYgfTWWkCAckULhs4IrUEVLRN2HrAZzq', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:4200', // the base url of the running ionic application. 
  }
};
