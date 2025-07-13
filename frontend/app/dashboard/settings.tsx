import { useState } from 'react'
import api from '@/lib/api'

// 用简单的自定义组件替代 antd
function Button({ children, ...props }: any) {
  return <button {...props} className="px-4 py-2 bg-blue-600 text-white rounded" />
}
function Input(props: any) {
  return <input {...props} className="border px-2 py-1 rounded" />
}
function Card({ title, children, className = '' }: any) {
  return (
    <div className={`border rounded shadow p-4 mb-4 ${className}`}>
      {title && <h2 className="font-bold text-lg mb-2">{title}</h2>}
      {children}
    </div>
  )
}
const message = {
  success: (msg: string) => alert(msg),
  error: (msg: string) => alert(msg),
  warning: (msg: string) => alert(msg),
}

export default function AccountSettings() {
  const [githubUsername, setGithubUsername] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [skills, setSkills] = useState<any[]>([])

  const handleConnectGithub = async () => {
    if (!githubUsername) {
      message.warning('请输入GitHub用户名')
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/users/connect/github', {
        username: githubUsername
      })
      setSkills(response.data.skills)
      message.success('GitHub账号绑定成功')
    } catch (error: unknown) {
      let msg = '绑定失败';
      if (error && typeof error === 'object' && 'message' in error) {
        msg += ': ' + (error as any).message
      }
      message.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <Card title="第三方账号绑定" className="mb-6">
        <div className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">GitHub</h3>
            <div className="flex gap-2">
              <Input
                placeholder="输入GitHub用户名"
                value={githubUsername}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGithubUsername(e.target.value)}
              />
              <Button 
                type="button" 
                disabled={isLoading}
                onClick={handleConnectGithub}
              >
                {isLoading ? '绑定中...' : '绑定账号'}
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {skills.length > 0 && (
        <Card title="技能分析结果">
          <div className="grid gap-4">
            {skills.map((skill, index) => (
              <div key={index} className="border p-4 rounded">
                <h4 className="font-medium">{skill.skill_name}</h4>
                <div className="flex items-center mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full" 
                      style={{ width: `${skill.proficiency}%` }}
                    ></div>
                  </div>
                  <span className="ml-2 text-sm">{skill.proficiency}%</span>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  <p>类别: {skill.category}</p>
                  {skill.evidence && typeof skill.evidence === 'object' &&
                    Object.entries(skill.evidence as Record<string, any>).map(([key, value]) => (
                      <p key={key}>{key}: {String(value)}</p>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
