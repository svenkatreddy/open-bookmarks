export const ENCRYPTED_FORMAT: string;
export const ENCRYPTION_CIPHER: string;
export const ENCRYPTION_KDF: string;
export const ENCRYPTION_ITERATIONS: number;
export const SALT_BYTES: number;
export const IV_BYTES: number;

export interface EncryptedPack {
  format?: string;
  cipher?: string;
  kdf?: string;
  iterations?: number;
  salt: string;
  iv: string;
  ciphertext: string;
}

export function encryptPack(jsonPack: Record<string, unknown>, password: string): Promise<EncryptedPack>;
export function decryptPack(encryptedPackage: EncryptedPack, password: string): Promise<Record<string, unknown>>;
export function isEncryptedPack(value: unknown): boolean;
