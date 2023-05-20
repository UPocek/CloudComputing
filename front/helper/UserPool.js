import { CognitoUserPool } from "amazon-cognito-identity-js"

const userPoolData = {
    UserPoolId: 'eu-central-1_R3ryoMSwI',
    ClientId: 'bsh3hotvgc668ukjncp5nda5q'
}

export default new CognitoUserPool(userPoolData);