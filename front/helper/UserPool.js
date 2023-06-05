import { CognitoUserPool } from "amazon-cognito-identity-js"

const userPoolData = {
    UserPoolId: 'eu-central-1_Z3VrKizkv',
    ClientId: '285soie9g3fc22jvmqivd8huhd'
}

export default new CognitoUserPool(userPoolData);