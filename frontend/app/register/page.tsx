'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { register } from '@/lib/auth';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (password.length < 8) {
      setError('密码长度不能少于8个字符');
      return;
    }

    setIsLoading(true);

    try {
      await register({ 
        username,
        email,
        password,
        full_name: username,
        current_role: 'Developer',
        target_role: 'Senior Developer',
        experience_years: 1
      });
      setSuccess('注册成功！即将跳转到登录页面...');
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } catch (err) {
      // 显示后端返回的具体错误信息
setError(err instanceof Error ? err.message : '注册失败，请检查输入信息或稍后重试');
console.error('Registration error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6 text-center">注册</h1>
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>
      )}
      {success && (
        <div className="bg-green-100 text-green-700 p-3 rounded mb-4">{success}</div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">用户名</label>
          <input
            type="text"
            value={username}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
            required
            minLength={3}
            maxLength={50}
            className="w-full px-3 py-2 border rounded-md text-gray-900"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">邮箱</label>
          <input
            type="email"
            value={email}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border rounded-md text-gray-900"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">密码</label>
          <input
            type="password"
            value={password}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-3 py-2 border rounded-md text-gray-900"
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 mb-2">确认密码</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-3 py-2 border rounded-md text-gray-900"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-400"
        >
          {isLoading ? '注册中...' : '注册'}
        </button>
      </form>
    </div>
  );
}
