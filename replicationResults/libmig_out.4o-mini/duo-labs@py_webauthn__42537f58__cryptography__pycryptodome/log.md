## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/duo-labs@py_webauthn__42537f58__cryptography__pycryptodome/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 13 files
### migrating tests/test_validate_certificate_chain.py
### migrating webauthn/authentication/verify_authentication_response.py
### migrating webauthn/helpers/algorithms.py
### migrating webauthn/helpers/decoded_public_key_to_cryptography.py
### migrating webauthn/helpers/pem_cert_bytes_to_open_ssl_x509.py
### migrating webauthn/helpers/validate_certificate_chain.py
### migrating webauthn/helpers/verify_signature.py
### migrating webauthn/registration/formats/android_key.py
### migrating webauthn/registration/formats/android_safetynet.py
### migrating webauthn/registration/formats/apple.py
### migrating webauthn/registration/formats/fido_u2f.py
### migrating webauthn/registration/formats/packed.py
### migrating webauthn/registration/formats/tpm.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_aaguid_to_string.py::TestAAGUIDToString::test_converts_bytes_to_uuid_format: passed != not found`
- `tests/test_base64url_to_bytes.py::TestWebAuthnBase64URLToBytes::test_converts_base64url_string_to_buffer: passed != not found`
- `tests/test_bytes_subclass_support.py::TestWebAuthnBytesSubclassSupport::test_handles_bytes_subclasses: passed != not found`
- `tests/test_bytes_subclass_support.py::TestWebAuthnBytesSubclassSupport::test_handles_memoryviews: passed != not found`
- `tests/test_bytes_to_base64url.py::TestWebAuthnBytesToBase64URL::test_converts_buffer_to_base64url_string: passed != not found`
- `tests/test_decode_credential_public_key.py::TestDecodeCredentialPublicKey::test_decode_rsa_public_key: passed != not found`
- `tests/test_decode_credential_public_key.py::TestDecodeCredentialPublicKey::test_decode_uncompressed_ec2_public_key: passed != not found`
- `tests/test_decode_credential_public_key.py::TestDecodeCredentialPublicKey::test_decodes_ec2_public_key: passed != not found`
- `tests/test_generate_authentication_options.py::TestWebAuthnGenerateAttestationOptions::test_generates_options_with_custom_values: passed != not found`
- `tests/test_generate_authentication_options.py::TestWebAuthnGenerateAttestationOptions::test_generates_options_with_defaults: passed != not found`
- `tests/test_generate_authentication_options.py::TestWebAuthnGenerateAttestationOptions::test_raises_on_empty_rp_id: passed != not found`
- `tests/test_generate_challenge.py::TestWebAuthnGenerateChallenge::test_generates_byte_sequence: passed != not found`
- `tests/test_generate_challenge.py::TestWebAuthnGenerateChallenge::test_generates_unique_value_each_time: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_generated_random_id_on_empty_user_id: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_generates_options_with_custom_values: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_generates_options_with_defaults: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_raises_on_empty_rp_id: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_raises_on_empty_rp_name: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_raises_on_empty_user_name: passed != not found`
- `tests/test_generate_registration_options.py::TestGenerateRegistrationOptions::test_raises_on_non_bytes_user_id: passed != not found`
- `tests/test_generate_user_handle.py::TestWebAuthnGenerateUserHandle::test_generates_byte_sequence: passed != not found`
- `tests/test_generate_user_handle.py::TestWebAuthnGenerateUserHandle::test_generates_unique_value_each_time: passed != not found`
- `tests/test_options_to_json.py::TestWebAuthnOptionsToJSON::test_converts_authentication_options_to_JSON: passed != not found`
- `tests/test_options_to_json.py::TestWebAuthnOptionsToJSON::test_converts_registration_options_to_JSON: passed != not found`
- `tests/test_options_to_json.py::TestWebAuthnOptionsToJSON::test_includes_optional_value_when_set: passed != not found`
- `tests/test_options_to_json.py::TestWebAuthnOptionsToJSON::test_raises_on_bad_input: passed != not found`
- `tests/test_parse_attestation_object.py::TestParseAttestationObject::test_can_parse_good_none_attestation_object: passed != not found`
- `tests/test_parse_attestation_object.py::TestParseAttestationObject::test_can_parse_good_packed_attestation_object: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_handles_authenticator_attachment: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_handles_bad_authenticator_attachment: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_handles_missing_user_handle: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_handles_user_handle: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_invalid_credential_type: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_missing_authenticator_data: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_missing_client_data_json: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_missing_id: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_missing_raw_id: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_missing_response: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_missing_signature: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_non_base64url_authenticator_data: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_non_base64url_client_data_json: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_non_base64url_raw_id: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_non_base64url_signature: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_raises_on_non_dict_json: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_success_from_dict: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_success_from_str: passed != not found`
- `tests/test_parse_authentication_credential_json.py::TestParseClientDataJSON::test_validates_credential_type: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_allow_credentials_entry_invalid_transports: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_allow_credentials_entry_invalid_transports_entry: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_allow_credentials_entry_missing_id: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_invalid_user_verification: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_missing_challenge: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_missing_user_verification: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_raises_on_non_dict_json: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_returns_parsed_options_full: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_returns_parsed_options_simple: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_supports_json_string: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_supports_optional_allow_credentials: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_supports_optional_rp_id: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_supports_optional_timeout: passed != not found`
- `tests/test_parse_authentication_options.py::TestParseAuthenticationOptionsJSON::test_supports_options_to_json_output: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_correctly_parses_attested_credential_data: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_correctly_parses_simple: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_parses_attested_credential_data_and_extension_data: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_parses_backup_state_flags: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_parses_bad_eddsa_auth_data: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_parses_only_extension_data: passed != not found`
- `tests/test_parse_authenticator_data.py::TestWebAuthnParseAuthenticatorData::test_parses_uv_false: passed != not found`
- `tests/test_parse_backup_flags.py::TestParseBackupFlags::test_raises_on_invalid_backup_state_flags: passed != not found`
- `tests/test_parse_backup_flags.py::TestParseBackupFlags::test_returns_multi_device_backed_up: passed != not found`
- `tests/test_parse_backup_flags.py::TestParseBackupFlags::test_returns_multi_device_not_backed_up: passed != not found`
- `tests/test_parse_backup_flags.py::TestParseBackupFlags::test_returns_single_device_not_backed_up: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_can_parse_attestation_client_data: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_include_token_binding_when_present: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_omit_cross_origin_if_not_present: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_omit_id_when_missing_from_token_binding: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_omit_token_binding_if_not_present: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_raises_exception_on_bad_json: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_require_status_in_token_binding_when_present: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_requires_challenge: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_requires_origin: passed != not found`
- `tests/test_parse_client_data_json.py::TestParseClientDataJSON::test_requires_type: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_handles_authenticator_attachment: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_handles_bad_authenticator_attachment: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_handles_missing_transports: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_ignores_non_list_transports: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_parses_transports: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_invalid_credential_type: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_missing_attestation_object: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_missing_client_data_json: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_missing_id: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_missing_raw_id: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_missing_response: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_non_base64url_attestation_object: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_non_base64url_client_data_json: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_non_base64url_raw_id: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_raises_on_non_dict_json: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_success_from_dict: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_success_from_str: passed != not found`
- `tests/test_parse_registration_credential_json.py::TestParseRegistrationCredentialJSON::test_validates_credential_type: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_exclude_credentials_entry_invalid_transports: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_exclude_credentials_entry_invalid_transports_entry: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_exclude_credentials_entry_missing_id: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_invalid_authenticator_selection_authenticator_attachment: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_invalid_authenticator_selection_require_resident_key: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_invalid_authenticator_selection_resident_key: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_invalid_authenticator_selection_user_verification: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_invalid_hints_assignment: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_invalid_hints_entry: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_malformed_rp_id: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_attestation: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_challenge: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_missing_rp_name: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_pub_key_cred_params: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_rp: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_user: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_user_display_name: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_user_id: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_missing_user_name: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_non_dict_json: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_pub_key_cred_params_entry_with_invalid_alg: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_raises_on_unrecognized_attestation: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_returns_parsed_options_full: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_returns_parsed_options_simple: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_empty_hints: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_json_string: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_missing_timeout: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_optional_authenticator_selection: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_optional_exclude_credentials: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_optional_hints: passed != not found`
- `tests/test_parse_registration_options_json.py::TestParseRegistrationOptionsJSON::test_supports_options_to_json_output: passed != not found`
- `tests/test_snake_case_to_camel_case.py::TestWebAuthnSnakeCaseToCamelCase::test_converts_client_data_json: passed != not found`
- `tests/test_snake_case_to_camel_case.py::TestWebAuthnSnakeCaseToCamelCase::test_converts_snake_case_to_camel_case: passed != not found`
- `tests/test_structs.py::TestStructsRegistrationCredential::test_parse_registration_credential_json: passed != not found`
- `tests/test_tpm_parse_cert_info.py::TestWebAuthnTPMParseCertInfo::test_properly_parses_cert_info_bytes: passed != not found`
- `tests/test_tpm_parse_pub_area.py::TestWebAuthnTPMParsePubArea::test_properly_parses_pub_area_bytes: passed != not found`
- `tests/test_validate_certificate_chain.py::TestValidateCertificateChain::test_passes_on_empty_root_certs_array: passed != not found`
- `tests/test_validate_certificate_chain.py::TestValidateCertificateChain::test_passes_on_no_root_certs: passed != not found`
- `tests/test_validate_certificate_chain.py::TestValidateCertificateChain::test_throws_on_bad_root_cert: passed != not found`
- `tests/test_validate_certificate_chain.py::TestValidateCertificateChain::test_validates_certificate_chain: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_raises_exception_on_incorrect_public_key: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_raises_exception_on_uv_required_but_false: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_supports_already_parsed_credential: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_supports_dict_credential: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_supports_multiple_expected_origins: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_verify_authentication_response_with_EC2_public_key: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_verify_authentication_response_with_OKP_public_key: passed != not found`
- `tests/test_verify_authentication_response.py::TestVerifyAuthenticationResponse::test_verify_authentication_response_with_RSA_public_key: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_raises_exception_on_unsupported_attestation_type: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_raises_useful_error_on_bad_attestation_object: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_raises_when_root_cert_invalid_for_response: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_supports_already_parsed_credential: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_supports_dict_credential: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_supports_multiple_expected_origins: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_verifies_none_attestation_response: passed != not found`
- `tests/test_verify_registration_response.py::TestVerifyRegistrationResponse::test_verifies_registration_over_cable: passed != not found`
- `tests/test_verify_registration_response_android_key.py::TestVerifyRegistrationResponseAndroidKey::test_verify_attestation_android_key: passed != not found`
- `tests/test_verify_registration_response_android_safetynet.py::TestVerifyRegistrationResponseAndroidSafetyNet::test_verify_attestation_android_safetynet: passed != not found`
- `tests/test_verify_registration_response_apple.py::TestVerifyRegistrationResponseApple::test_verify_attestation_apple_passkey: passed != not found`
- `tests/test_verify_registration_response_fido_u2f.py::TestVerifyRegistrationResponseFIDOU2F::test_verify_attestation_from_fido_conformance: passed != not found`
- `tests/test_verify_registration_response_fido_u2f.py::TestVerifyRegistrationResponseFIDOU2F::test_verify_attestation_from_yubikey_firefox: passed != not found`
- `tests/test_verify_registration_response_fido_u2f.py::TestVerifyRegistrationResponseFIDOU2F::test_verify_attestation_with_unsupported_token_binding: passed != not found`
- `tests/test_verify_registration_response_fido_u2f.py::TestVerifyRegistrationResponseFIDOU2F::test_verify_attestation_with_unsupported_token_binding_status: passed != not found`
- `tests/test_verify_registration_response_packed.py::TestVerifyRegistrationResponsePacked::test_verify_attestation_from_yubikey_firefox: passed != not found`
- `tests/test_verify_registration_response_packed.py::TestVerifyRegistrationResponsePacked::test_verify_attestation_with_okp_public_key: passed != not found`
- `tests/test_verify_registration_response_tpm.py::TestVerifyRegistrationResponseTPM::test_verify_attestation_dell_xps_13: passed != not found`
- `tests/test_verify_registration_response_tpm.py::TestVerifyRegistrationResponseTPM::test_verify_attestation_lenovo_carbon_x1: passed != not found`
- `tests/test_verify_registration_response_tpm.py::TestVerifyRegistrationResponseTPM::test_verify_attestation_surface_pro_4: passed != not found`
- `tests/test_verify_registration_response_tpm.py::TestVerifyRegistrationResponseTPM::test_verify_tpm_with_ecc_public_area_type: passed != not found`
- `tests/test_verify_safetynet_timestamp.py::TestVerifySafetyNetTimestamp::test_does_not_raise_on_last_possible_millisecond: passed != not found`
- `tests/test_verify_safetynet_timestamp.py::TestVerifySafetyNetTimestamp::test_does_not_raise_on_timestamp_slightly_in_future: passed != not found`
- `tests/test_verify_safetynet_timestamp.py::TestVerifySafetyNetTimestamp::test_does_not_raise_on_timestamp_slightly_in_past: passed != not found`
- `tests/test_verify_safetynet_timestamp.py::TestVerifySafetyNetTimestamp::test_raises_on_timestamp_too_far_in_future: passed != not found`
- `tests/test_verify_safetynet_timestamp.py::TestVerifySafetyNetTimestamp::test_raises_on_timestamp_too_far_in_past: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
